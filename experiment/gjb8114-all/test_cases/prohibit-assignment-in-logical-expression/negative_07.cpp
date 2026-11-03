bool fetch() {
    return true;
}

int main() {
    bool value = false;
    if (!(value = fetch())) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-3]
        return 1;
    }
    return 0;
}
