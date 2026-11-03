void process(int speedO,
             int speed0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-10]
    (void)speedO;
    (void)speed0;
}

int main() {
    process(1, 2);
    return 0;
}
