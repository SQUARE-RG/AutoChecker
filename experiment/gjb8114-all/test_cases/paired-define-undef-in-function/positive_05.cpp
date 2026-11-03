class Calculator
{
public:
    unsigned int compute() const
    {
        unsigned int result = 0U;
#define CLASS_MACRO 4U
        result = result + CLASS_MACRO;
#undef CLASS_MACRO
        return result;
    }
};

int main()
{
    Calculator calculator;
    return (calculator.compute() == 4U) ? 0 : 1;
}
