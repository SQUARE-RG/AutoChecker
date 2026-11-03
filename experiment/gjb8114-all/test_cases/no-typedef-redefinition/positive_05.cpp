namespace first_ns {
typedef int index_type;

index_type get_index()
{
    return 7;
}

namespace second_ns {
typedef float ratio_type;

ratio_type get_ratio()
{
    return 0.25f;
}
} // namespace second_ns
} // namespace first_ns

int main()
{
    first_ns::index_type i = first_ns::get_index();
    first_ns::second_ns::ratio_type r = first_ns::second_ns::get_ratio();
    return (i == 7 && r > 0.0f) ? 0 : 1;
}
