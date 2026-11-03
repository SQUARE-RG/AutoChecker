int main() {
    double dData = 0.0;
    double* pData = &dData;
    float fData;
    fData = *pData; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-3]
    return 0;
}
