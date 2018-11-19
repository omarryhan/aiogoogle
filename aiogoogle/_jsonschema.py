from jsonschema import _validators
import jsonschema

def minimum(validator, minimum, instance, schema):
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


def maximum(validator, maximum, instance, schema):
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

def patch():
    _validators.minimum = minimum
    _validators.maximum = maximum