void set_handler(int id, void (*)(int)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-13]

int main() {
    set_handler(1, nullptr);
    return 0;
}

void set_handler(int id, void (*callback)(int)) {
    (void)id;
    (void)callback;
}
