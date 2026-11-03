int shared_counter = 0;

template <typename T>
T read_shared_counter() {
    extern int shared_counter; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-17]
    return shared_counter;
}

int main() {
    return read_shared_counter<int>();
}
