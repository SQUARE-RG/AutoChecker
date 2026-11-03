template <typename T>
T read_first(T* ptr) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-2]
    return *ptr;
}

int main() {
    int value = 7;
    return read_first(&value) == 7 ? 0 : 1;
}
