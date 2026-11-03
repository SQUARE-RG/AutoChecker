typedef int SINT_32;

SINT_32 compute() {
    SINT_32 result = 0;
    double scale = 1.0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-1]
    result = static_cast<SINT_32>(scale);
    return result;
}
