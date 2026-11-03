// Namespace-scope variable used as the control variable of a for loop.

namespace state
{
    int index = 3;
}

int main()
{
    int total = 0;
    for (state::index = 10; state::index > 0; state::index--) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-1]
    {
        total += state::index;
    }
    return total;
}
