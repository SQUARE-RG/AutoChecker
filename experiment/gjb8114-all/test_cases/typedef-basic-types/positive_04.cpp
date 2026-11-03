typedef int SINT_32;

SINT_32 main() {
    SINT_32 value = 0;
    SINT_32* pValue = &value;
    *pValue = 5;
    return value;
}
