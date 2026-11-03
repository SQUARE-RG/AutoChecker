template <class T> using identity_t = T;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-1]

int main() {
    identity_t<int> value = 42;
    return value;
}
