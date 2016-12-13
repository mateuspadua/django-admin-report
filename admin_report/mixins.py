# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
# from django.db.models.query import ValuesQuerySet
from django.db.models import Sum, Avg, Count, Max, Min
# from django.contrib.admin.validation import ModelAdminValidator
from django.http import Http404, HttpResponseRedirect
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.exceptions import SuspiciousOperation, ImproperlyConfigured
from daterange_filter.filter import DateRangeFilter
from django.db.models import ForeignKey
from django.db.models.constants import LOOKUP_SEP
from django.db.models.sql.constants import QUERY_TERMS
import copy
import types
import uuid
import sys
from django.utils import formats

map_aggregates = ((Sum, "__sum"), (Count, "__count"), (Avg, "__avg"), (Max, "__max"), (Min, "__min"))


def function_builder(name_function, attr, title_column):
    def new_function(self, obj):
        return getattr(obj, attr)
    new_function.__name__ = name_function
    if title_column:
        new_function.short_description = title_column
    new_function.admin_order_field = attr
    new_function.allow_tags = True
    return new_function


class ChangeListChartReport(ChangeList):

    result_aggregate = []

    def get_queryset(self, request):

        # qs = super(self.__class__, self).get_queryset(request)
        # First, we collect all the declared list filters.
        (self.filter_specs, self.has_filters, remaining_lookup_params,
            filters_use_distinct) = self.get_filters(request)

        # Then, we let every list filter modify the queryset to its liking.

        qs = self.root_queryset
        # print "#### qs antes ####"
        # print qs.query
        all_query = {}
        for filter_spec in self.filter_specs:
            # print "---- filter_spec ----"
            # print filter_spec.used_parameters
            if filter_spec.used_parameters and filter_spec.used_parameters.values()[0]:
                if isinstance(filter_spec, DateRangeFilter):
                    if filter_spec.form.is_valid():
                        # get no null params
                        filter_params = dict(filter(lambda x: bool(x[1]),
                                                    filter_spec.form.cleaned_data.items()))
                        all_query.update(**filter_params)
                else:
                    all_query.update(filter_spec.used_parameters)

            # comentando a versao do Django, pois da maneira abaixo ele intercala os join gerando joins extras, o que resulta em um resultado errado, nas agregaçoes SUM, COUNT, etc...
            # new_qs = filter_spec.queryset(request, qs)
            # if new_qs is not None:
            #     qs = new_qs

        # coloca o dicionário de uma vez só, assim dessa forma não há problema de criar joins "desnessárias" para filtros que apontam para as mesma tabelas estrangeiras
        # como explicado logo acima
        qs = qs.filter(**all_query)

        # print "#### qs depois ####"
        # print qs.query

        try:
            # Finally, we apply the remaining lookup parameters from the query
            # string (i.e. those that haven't already been processed by the
            # filters).
            qs = qs.filter(**remaining_lookup_params)
        except (SuspiciousOperation, ImproperlyConfigured):
            # Allow certain types of errors to be re-raised as-is so that the
            # caller can treat them in a special way.
            raise
        except Exception as e:
            # Every other error is caught with a naked except, because we don't
            # have any other way of validating lookup parameters. They might be
            # invalid if the keyword arguments are incorrect, or if the values
            # are not in the correct type, so we might get FieldError,
            # ValueError, ValidationError, or ?.
            raise IncorrectLookupParameters(e)

        if not qs.query.select_related:
            qs = self.apply_select_related(qs)

        # Set ordering.
        ordering = self.get_ordering(request, qs)
        qs = qs.order_by(*ordering)

        # Apply search results
        qs, search_use_distinct = self.model_admin.get_search_results(
            request, qs, self.query)

        # Remove duplicates from results, if necessary
        if filters_use_distinct | search_use_distinct:
            qs = qs.distinct()

        if self.model_admin.annotate_fields:
            # qs = self.root_queryset

            # all_used_parameters = {}
            # qs = self.root_queryset
            # (self.filter_specs, self.has_filters, remaining_lookup_params, filters_use_distinct) = self.get_filters(request)
            # for filter_spec in self.filter_specs:
            #     # props = ['choices', 'create', 'expected_parameters', 'field', 'field_path', 'has_output', 'lookup_kwarg', 'lookup_val', 'queryset', 'register', 'template', 'title', 'used_parameters']
            #     # for p in props:
            #     #    print "{0}: {1}".format(p, getattr(filter_spec, p))
            #     # print "#####################################################"
            #     new_qs = filter_spec.queryset(request, qs)
            #     if new_qs is not None:
            #         qs = new_qs
            #     all_used_parameters.update(filter_spec.used_parameters)

            # if all_used_parameters:
            #     qs = qs.filter(**all_used_parameters)

            # estudar essa parte, esta estranho
            if self.model_admin.group_by:
                qs = qs.values(*self.model_admin.group_by)

            # faz uma copia antes de chamar o metodo annotate, pois para campos aggregate que não
            # representam um campo annotate, não se pode ter o annotate na query
            self.query_to_normal_aggregate = qs

            qs = qs.annotate(*self.model_admin.annotate_fields_2, **self.model_admin.annotate_fields)

            # Set ordering.
            ordering = self.get_ordering(request, qs)
            qs = qs.order_by(*ordering)

            # Apply search results
            qs, search_use_distinct = self.model_admin.get_search_results(request, qs, self.query)

            # print qs.query
            # print "get_queryset"
        else:
            self.query_to_normal_aggregate = qs

        # print "#### query final ####"
        # print qs.query

        return qs

    def get_results(self, request):
        super(self.__class__, self).get_results(request)

        # print self.result_list[0].pedidoitem__valor_unitario_sem_descontos__avg
        # print self.result_list[0].pedidoitem__valor_unitario_sem_descontos__max

        # print "get_results"
        # print self.queryset.query

        if self.result_list and isinstance(self.result_list[0], dict):
            pk_name = self.model._meta.pk.name
            try:
                ids = [i[pk_name] for i in self.result_list]
            except KeyError:
                ids = []

            result_list_in_model = self.model.objects.filter(pk__in=ids)
            result_list_in_model_dict = {}
            for item_model in result_list_in_model:
                result_list_in_model_dict[getattr(item_model, pk_name)] = item_model

            # print "result_list_in_model_dict ========="
            # print result_list_in_model_dict

            new_result_list = []
            for row in self.result_list:
                if pk_name in row and result_list_in_model_dict:
                    new_row = copy.deepcopy(result_list_in_model_dict[row[pk_name]])
                else:
                    new_row = self.model()

                for key, value in list(row.items()):
                    # if hasattr(new_row, key):
                    #     print self.model._meta.get_field(key)
                    #     field_object, model, direct, m2m = self.model._meta.get_field_by_name(key)
                    #     if (m2m or isinstance(field_object, ForeignKey)) is True:
                    #         continue

                    setattr(new_row, key, value)

                new_result_list.append(new_row)

            self.result_list = new_result_list

        self.get_result_aggregate()

    def get_result_aggregate(self):
        # print self.list_display

        result_aggregate = []
        result_aggregate_queryset = None
        result_aggregate_from_normal_queryset = {}
        result_aggregate_from_annotate_queryset = {}
        # from django.db import connection
        # connection.queries = []
        qs = self.queryset
        if self.model_admin.aggregate_fields_from_normal:
            # print "normal"
            result_aggregate_from_normal_queryset = self.query_to_normal_aggregate.aggregate(*self.model_admin.aggregate_fields_from_normal)
            # print "########## result_aggregate_from_normal_queryset ##########"
            # print result_aggregate_from_normal_queryset

        if self.model_admin.aggregate_fields_from_annotate:
            # print "annotate"
            result_aggregate_from_annotate_queryset = qs.aggregate(*self.model_admin.aggregate_fields_from_annotate)
            # print "########## result_aggregate_from_annotate_queryset ##########"
            # print result_aggregate_from_annotate_queryset

        # print "#######"
        # print qs.query
        # print connection.queries

        result_aggregate_queryset = dict(result_aggregate_from_normal_queryset, **result_aggregate_from_annotate_queryset)

        # print result_aggregate_queryset

        if result_aggregate_queryset:
            for column in self.list_display:
                result_aggregate_temp = None
                if column in self.model_admin.map_display_fields_and_aggregate:
                    for aggregate in self.model_admin.map_display_fields_and_aggregate[column]:
                        # clean_name_field = aggregate[0][:-len(aggregate[0][aggregate[0].rfind("__"):])]
                        pos_value_place_holder = aggregate[2].find("%value")

                        aggregate_string_replace = "<strong>{0}:</strong> {1}"
                        if pos_value_place_holder != -1:
                            aggregate_string_replace = aggregate[2].replace("%value", "{1}")

                        if isinstance(result_aggregate_queryset[aggregate[0]], float):
                            label_foot = formats.number_format(result_aggregate_queryset[aggregate[0]], 2)
                        else:
                            label_foot = formats.localize(result_aggregate_queryset[aggregate[0]], use_l10n=True)

                        label_foot = aggregate_string_replace.format(aggregate[2], label_foot)
                        result_aggregate_temp = "{0}<br>{1}".format(result_aggregate_temp, label_foot) if result_aggregate_temp else label_foot
                    # print "@@@@@@@@@@@@@@@@@@@@@@@"
                if result_aggregate_temp:
                    result_aggregate.append(result_aggregate_temp)
                else:
                    result_aggregate.append("")

        # print "################### result_aggregate #####################"
        # print result_aggregate
        self.result_aggregate = result_aggregate


# class ModelAdminValidator2(ModelAdminValidator):
#     def validate_list_display(self, cls, model):
#         # super(ModelAdminValidator2, self).validate_list_display(cls, model)
#         pass


class AdminExceptionFieldsFilterMixin(admin.ModelAdmin):

    exception_fields_filter = ()

    def lookup_allowed(self, lookup, value):
        # ret = super(AdminExceptionFieldsFilterMixin, self).lookup_allowed(lookup, value)
        # if not ret and self.exception_fields_filter:
        #     parts = lookup.split(LOOKUP_SEP)

        #     if len(parts) > 1 and parts[-1] in QUERY_TERMS:
        #         parts.pop()
        #         clean_lookup = LOOKUP_SEP.join(parts)
        #         if clean_lookup in self.exception_fields_filter:
        #             return True
        # return ret
        return True


class ChartReportAdmin(admin.ModelAdmin):
    # change_list_template = "admin/relatorios/change_list.html"

    report_annotates = ()
    report_aggregates = ()
    group_by = ()
    list_display_links = None
    # validator_class = ModelAdminValidator2

    # def __new__(cls, *args, **kwargs):
        # return super(ChartReportAdmin, cls).__new__(cls, *args, **kwargs)

    class Media:
        css = {
            'all': ('admin/css/django_admin_report/django_admin_report.css',)
        }

    def __init__(self, model, admin_site):
        # print "########################### report_annotates ###############################"
        # print self.report_annotates
        self.annotate_fields = {}
        self.annotate_fields_2 = []
        # self.aggregate_fields = []
        self.aggregate_fields_from_normal = []
        self.aggregate_fields_from_annotate = []
        self.map_annotate_fields = {}
        self.map_display_fields_and_aggregate = {}

        for annotate in self.report_annotates:
            for func, end_field_name in map_aggregates:
                if func == annotate[1]:
                    name_field_annotate = "{0}{1}".format(annotate[0], end_field_name)
                    new_name_field_annotate = "{0}_{1}".format(annotate[0].replace("__", "_"), str(uuid.uuid4()).replace("-", "")[:10])
                    self.map_annotate_fields.update({name_field_annotate: new_name_field_annotate})
                    self.annotate_fields.update({new_name_field_annotate: annotate[1](annotate[0])})
                    self.annotate_fields_2.append(annotate[1](annotate[0]))
                    self.addMethod(function_builder(name_field_annotate, new_name_field_annotate, annotate[2] if len(annotate) == 3 else None))
                    break

        for aggregate in self.report_aggregates:
            for func, end_field_name in map_aggregates:
                if func == aggregate[1]:
                    copy_aggregate = list(aggregate[:])
                    if aggregate[0] in self.map_annotate_fields:
                        new_name_field = self.map_annotate_fields[aggregate[0]]
                    else:
                        new_name_field = aggregate[0]
                    name_field_aggregate = "{0}{1}".format(new_name_field, end_field_name)

                    copy_aggregate[0] = name_field_aggregate

                    new_label = "{0}{1}".format(aggregate[0], end_field_name)
                    if len(copy_aggregate) == 2:
                        copy_aggregate.append(new_label)
                    elif not copy_aggregate[2]:
                        copy_aggregate[2] = new_label

                    if len(copy_aggregate) == 4:  # significa que foi especificado em qual coluna deve aparecer o valor agregado
                        column_display_list = aggregate[3]
                    else:
                        column_display_list = aggregate[0]
                        if column_display_list not in self.list_display:
                            column_display_list = new_label

                    if column_display_list not in self.map_display_fields_and_aggregate:
                        self.map_display_fields_and_aggregate[column_display_list] = []

                    self.map_display_fields_and_aggregate[column_display_list].append(copy_aggregate)
                    break

            if aggregate[0] in self.map_annotate_fields:
                new_name_field = self.map_annotate_fields[aggregate[0]]
                self.aggregate_fields_from_annotate.append(aggregate[1](new_name_field))
            else:
                self.aggregate_fields_from_normal.append(aggregate[1](aggregate[0]))

        # print self.aggregate_fields_from_normal
        # print self.aggregate_fields_from_annotate
        # print "########################## self.map_display_fields_and_aggregate #########################"
        # print self.map_display_fields_and_aggregate

        # ChartReportAdmin.addMethod(function_builder("total_value__sum"))

        self.list_max_show_all = sys.maxsize

        super(ChartReportAdmin, self).__init__(model, admin_site)

    # TODO: refazer esse metodo, nao esta legal
    def add_view(self, request, form_url='', extra_context=None):
        return HttpResponseRedirect(request.META["HTTP_REFERER"])  # volta sempre para a mesma pagina

    def addMethod(self, func):
        return setattr(self, func.__name__, types.MethodType(func, self))

    def get_changelist(self, request, **kwargs):
        return ChangeListChartReport
