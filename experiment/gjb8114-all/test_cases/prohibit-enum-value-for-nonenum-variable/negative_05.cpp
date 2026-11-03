enum Status { ok = 1, fail = 2 };

void consume(unsigned int code) {
    (void)code;
}

int main() {
    consume(ok); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-11]
    return 0;
}
