from jsonschema import _validators
import jsonschema

def minimum(validator, minimum, instance, schema):
    #  REPLACES:
    #
    #def minimum(validator, minimum, instance, schema):
    #    if not validator.is_type(instance, "number"):
    #        return
    #
    #    if instance < minimum:
    #        yield ValidationError(
    #            "%r is less than the minimum of %r" % (instance, minimum)
    #        )
    #
    if not validator.is_type(instance, "string"):
        return

    try:
        if instance < str(minimum):
            yield jsonschema.ValidationError(
                "%r is less than the minimum of %r" % (instance, minimum)
            )
    except ValueError:
        yield jsonschema.ValidationError(
            "%r is less than the minimum of %r" % (instance, minimum)
        )



def maximum(validator, maximum, instance, schema):
    #   REPLACES:
    #
    #def maximum(validator, maximum, instance, schema):
    #    if not validator.is_type(instance, "number"):
    #        return
    #
    #    if instance > maximum:
    #        yield ValidationError(
    #            "%r is greater than the maximum of %r" % (instance, maximum)
    #        )
    #
    if not validator.is_type(instance, "string"):
        return

    try:
        if instance > int(maximum):
            yield jsonschema.ValidationError(
                "%r is greater than the maximum of %r" % (instance, maximum)
            )
    except ValueError:
        yield jsonschema.ValidationError(
            "%r is less than the maximum of %r" % (instance, minimum)
        )

#draft3_type_checker = _types.TypeChecker(
#    {
#        u"any": _types.is_any,
#        u"array": _types.is_array,
#        u"boolean": _types.is_bool,
#        u"integer": _types.is_integer,
#        u"object": _types.is_object,
#        u"null": _types.is_null,
#        u"number": _types.is_number,
#        u"string": _types.is_string,
#    },
#)


def patch():
    #_validators.minimum = minimum
    #_validators.maximum = maximum
    #_types.draft3_type_checker = draft3_type_checker 
    pass