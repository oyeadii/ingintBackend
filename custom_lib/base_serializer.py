import numbers
from rest_framework import serializers
from custom_lib.helper import camel_case_to_snake_case


class BaseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        non_null_ret = {}
        for key in ret.keys():
            if ret[key] or isinstance(ret[key], numbers.Number):
                non_null_ret[camel_case_to_snake_case(key)] = ret[key]
        return non_null_ret