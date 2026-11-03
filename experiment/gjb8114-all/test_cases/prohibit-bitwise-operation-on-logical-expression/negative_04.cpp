bool check(bool a, bool b) {
    bool result = ~(a && b); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-4]
    return result;
}

int main() {
    return check(true, false) ? 0 : 1;
}
