template <typename T>
T add_template_constant(T value)
{
#define TEMPLATE_PAIRED_CONSTANT 4U
    T result = value + static_cast<T>(TEMPLATE_PAIRED_CONSTANT);
#undef TEMPLATE_PAIRED_CONSTANT
    return result;
}

int main()
{
    return add_template_constant<int>(1);
}
