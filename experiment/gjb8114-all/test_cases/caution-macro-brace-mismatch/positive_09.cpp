#define DEFINE_NS(ns) namespace ns { int value = 1; }

DEFINE_NS(test_ns)

int main()
{
    return test_ns::value;
}
