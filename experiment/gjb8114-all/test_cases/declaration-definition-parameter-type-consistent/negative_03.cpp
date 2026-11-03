void reset(int* ptr);

void reset(long* ptr) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-5]
{
    if (ptr != nullptr) {
        *ptr = 0;
    }
}

int main()
{
    long value = 1;
    reset(&value);
    return 0;
}
