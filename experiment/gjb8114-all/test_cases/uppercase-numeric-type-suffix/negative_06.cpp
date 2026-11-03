int main() {
    auto value = 077l; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-5]
    return value == 63L ? 0 : 1;
}
