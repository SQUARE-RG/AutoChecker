int* returnAddressOfConstLocal() {
    const int local = 11;
    return const_cast<int*>(&local); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-4]
}
