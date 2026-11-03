int computeSum() noexcept { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-23]
    return 1;
}

int main(void) {
    return computeSum();
}
