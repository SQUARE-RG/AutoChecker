// negative_06.cpp
typedef int SINT;

SINT increment(SINT value) {
    return value + 1;
}

void useFunctionPointer() {
    int (*funcPtr)(int) = increment; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-1]
    auto result = funcPtr(41);
    (void)result;
}
