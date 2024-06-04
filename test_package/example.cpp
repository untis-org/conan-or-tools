#include <omp.h>
#include "iostream"
#include <ortools/base/logging.h>
#include <ortools/linear_solver/linear_solver.h>

double run(operations_research::MPSolver::OptimizationProblemType problemType, bool log)
{
    // Create the linear solver with the GLOP backend.
    operations_research::MPSolver solver("simple_lp_program", problemType);

    // Create the variables x and y.
    auto *const x = solver.MakeNumVar(0.0, 1, "x");
    auto *const y = solver.MakeNumVar(0.0, 2, "y");

    if (log)
        LOG(INFO) << "Number of variables = " << solver.NumVariables();

    // Create a linear constraint, 0 <= x + y <= 2.
    auto *const ct = solver.MakeRowConstraint(0.0, 2.0, "ct");
    ct->SetCoefficient(x, 1);
    ct->SetCoefficient(y, 1);

    if (log)
        LOG(INFO) << "Number of constraints = " << solver.NumConstraints();

    // Create the objective function, 3 * x + y.
    operations_research::MPObjective *const objective = solver.MutableObjective();
    objective->SetCoefficient(x, 3);
    objective->SetCoefficient(y, 1);
    objective->SetMaximization();

    solver.Solve();

    if (log)
    {
        LOG(INFO) << "Solution:" << std::endl;
        LOG(INFO) << "Objective value = " << objective->Value();
        LOG(INFO) << "x = " << x->solution_value();
        LOG(INFO) << "y = " << y->solution_value();
    }

    return y->solution_value();
}

int main()
{
    bool log_output = true;
    absl::SetFlag(&FLAGS_stderrthreshold, true);
    std::cout << "GLOP" << std::endl;
    run(operations_research::MPSolver::GLOP_LINEAR_PROGRAMMING, log_output);
    std::cout << "\n\n\n"
              << std::endl;

    std::cout << "CLP" << std::endl;
    auto certificate = run(operations_research::MPSolver::CLP_LINEAR_PROGRAMMING, log_output);
    std::cout << "\n\n\n"
              << std::endl;

    int number_of_runs = 2;
    std::cout << "parallel CLP (" << number_of_runs << " runs)" << std::endl;
    log_output = false;
    std::vector<double> return_values(number_of_runs);
#pragma omp parallel for
    for (int i = 0; i < number_of_runs; i++)
        return_values[i] = run(operations_research::MPSolver::CLP_LINEAR_PROGRAMMING, log_output);

    int failed_instances = 0;
    for (auto returned : return_values)
        if (std::fabs(returned - certificate) > 1.e-8)
        {
            std::cout << "off by " << std::fabs(returned - certificate) << "(" << returned << " vs " << certificate << ")" << std::endl;
            failed_instances++;
        }

    std::cout << "parallel CLP done (" << failed_instances << " failed instances)." << std::endl;

    return EXIT_SUCCESS;
}