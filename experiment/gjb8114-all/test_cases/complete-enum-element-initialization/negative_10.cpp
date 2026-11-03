#include <cstdlib>

constexpr int kReadyValue = 5;

enum class Status
{
    Unknown,
    Ready = kReadyValue, // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-4]
    Done
};

int main()
{
    Status s = Status::Done;
    (void)s;
    return EXIT_SUCCESS;
}
