int main() {
    register int counter = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-2]
    counter += 1;
    return counter;
}
