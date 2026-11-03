int* localArrayDecay()
{
    int buffer[3] = {1, 2, 3};
    return buffer; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-4]
}
