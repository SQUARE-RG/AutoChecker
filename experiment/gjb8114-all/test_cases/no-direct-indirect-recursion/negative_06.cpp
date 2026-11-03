struct Count {
    int value;
};

Count operator+(const Count& lhs, const Count& rhs) {
    return lhs + rhs; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-16]
}

int main() {
    return 0;
}
