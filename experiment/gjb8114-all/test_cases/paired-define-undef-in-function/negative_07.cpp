template <typename T>
T add_template_offset(T value)
{
#define TEMPLATE_LOCAL_OFFSET 3U // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-6]
    return value + static_cast<T>(TEMPLATE_LOCAL_OFFSET);
}

int main()
{
    return add_template_offset<int>(1);
}
