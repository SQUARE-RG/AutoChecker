// positive_06.cpp
typedef int SINT;
typedef SINT (*SIntUnaryFn)(SINT);

SINT increment(SINT value) {
    return value + 1;
}

void useFunctionPointer() {
    SIntUnaryFn funcPtr = increment;
    auto result = funcPtr(41);
    (void)result;
}
