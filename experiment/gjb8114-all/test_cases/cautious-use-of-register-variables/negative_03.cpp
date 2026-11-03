int add(register int lhs, int rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-2]
    return lhs + rhs;
}

int main() {
    return add(1, 2);
}
