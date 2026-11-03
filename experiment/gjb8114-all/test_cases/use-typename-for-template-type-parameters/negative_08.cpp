template <class... Ts>  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-1]
void ignore(Ts... args) {
    (void)(sizeof...(args));
}

int main() {
    ignore(1, 2.0, 'c');
    return 0;
}
