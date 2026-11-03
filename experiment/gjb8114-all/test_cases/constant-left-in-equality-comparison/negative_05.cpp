bool is_enabled(bool flag) {
    return flag == true; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-12-1]
}

int main() {
    return is_enabled(false) ? 0 : 1;
}
