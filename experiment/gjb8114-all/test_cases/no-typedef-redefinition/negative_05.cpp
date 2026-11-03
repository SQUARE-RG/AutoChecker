namespace outer_ns {
typedef int mytype;

namespace inner_ns {
typedef float mytype; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-3]

float get_value()
{
    mytype value = 1.5f;
    return value;
}
} // namespace inner_ns
} // namespace outer_ns

int main()
{
    return static_cast<int>(outer_ns::inner_ns::get_value());
}
