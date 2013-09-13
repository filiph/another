. ./config.sh
$GIMP_PATH --verbose -i -b '(apply-painting '\"${1}\"')' -b '(gimp-quit 0)'
