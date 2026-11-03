typedef int SINT_32;
typedef double FLOAT_64;

SINT_32 compute(FLOAT_64 scale) {
    SINT_32 result = static_cast<SINT_32>(scale);
    return result;
}
