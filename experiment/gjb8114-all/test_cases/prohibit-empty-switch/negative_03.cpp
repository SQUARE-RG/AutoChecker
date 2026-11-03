// negative_03.cpp
namespace {

int count_kind(unsigned char kind)
{
    switch (kind) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-3]
    {
    }
    return 0;
}

}

int main()
{
    return count_kind('a');
}
