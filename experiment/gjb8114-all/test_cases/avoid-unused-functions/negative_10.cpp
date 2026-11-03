namespace {
template <typename T>
T identity(T v) {
    return v;
}

template <>
const char* identity<const char*>(const char* v) { return v; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-3]
}

int main() {
    return identity(7);
}
