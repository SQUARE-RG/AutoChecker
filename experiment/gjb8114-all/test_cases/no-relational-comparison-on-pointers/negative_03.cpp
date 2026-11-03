struct Sample
{
    int value;
};

int choose(Sample* first, Sample* second)
{
    if (first >= second) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-2]
    {
        return first->value;
    }
    return second->value;
}
