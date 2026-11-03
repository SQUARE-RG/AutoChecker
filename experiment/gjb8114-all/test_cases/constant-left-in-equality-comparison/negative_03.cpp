int main() {
    char grade = 'A';
    if (grade == 'A') { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-12-1]
        return 0;
    }
    return 1;
}
