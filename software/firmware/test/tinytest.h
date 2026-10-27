/* Minimal assert harness (Unity/CMock per §12 can replace it; this keeps the host build dependency-free). */
#ifndef TINYTEST_H
#define TINYTEST_H
#include <stdio.h>
extern int tt_fail, tt_checks;
#define CHECK(c) do { tt_checks++; if (!(c)) { tt_fail++; printf("  FAIL %s:%d: %s\n", __FILE__, __LINE__, #c); } } while (0)
#define CHECK_EQ(a, b) do { tt_checks++; long long _a = (long long)(a), _b = (long long)(b); \
    if (_a != _b) { tt_fail++; printf("  FAIL %s:%d: %s == %s (%lld != %lld)\n", __FILE__, __LINE__, #a, #b, _a, _b); } } while (0)
#define RUN(t) do { int _f = tt_fail; hal_mock_reset(); t(); printf("%s %s\n", tt_fail == _f ? "ok  " : "FAIL", #t); tt_tests++; } while (0)
extern int tt_tests;
#endif
