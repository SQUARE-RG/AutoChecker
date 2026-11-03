int main() {
    double dValue = 0.0;
    float fValues[2] = {0.0f, 0.0f};
    fValues[0] = dValue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-3]
    return 0;
}
