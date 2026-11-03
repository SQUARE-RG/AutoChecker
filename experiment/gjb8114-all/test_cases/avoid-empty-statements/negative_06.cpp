int main() {
    int count = 0;
    do ; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-1]
    while (++count < 3);
    return count;
}
