template <typename T>
void fillAll(T* p) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-5]
{
    for (int i = 0; i < 5; ++i) {
        p[i] = T{};
    }
}

int main() {
    int values[5] = {1, 2, 3, 4, 5};
    fillAll(values);
    return 0;
}
