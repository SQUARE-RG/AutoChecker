enum Code { first = 10, second = 20 };

unsigned int getCode() {
    return first; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-11]
}

int main() {
    unsigned int value = getCode();
    (void)value;
    return 0;
}
