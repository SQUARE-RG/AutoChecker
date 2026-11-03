int*** get_ptr() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-1]
    return nullptr;
}

int main() {
    return 0;
}
