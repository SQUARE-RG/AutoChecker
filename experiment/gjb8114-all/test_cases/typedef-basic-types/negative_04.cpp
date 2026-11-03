typedef int SINT_32;

SINT_32 main() {
    SINT_32 value = 0;
    int* pValue = &value;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-1]
    *pValue = 5;
    return value;
}
