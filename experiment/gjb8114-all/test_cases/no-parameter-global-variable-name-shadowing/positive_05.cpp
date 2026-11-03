namespace sample {

int scale = 10;

int apply(int factor)
{
    return scale * factor;
}

} // namespace sample

int main()
{
    return sample::apply(3);
}
