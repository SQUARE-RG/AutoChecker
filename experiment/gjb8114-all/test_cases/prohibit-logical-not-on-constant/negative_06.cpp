enum Color { Black, White };

int main() {
    bool flag = !Black; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-10]
    return flag ? 0 : 1;
}
