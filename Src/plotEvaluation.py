import matplotlib.pyplot as plt

def plot_bids_per_round(all_bids):
    """
    Plots the number of bids per round.

    Args:
        all_bids (list): A list of bids, where each bid contains a 'round_last_bid' key.
    """
    rounds = [bid['round_last_bid'] for bid in all_bids]
    plt.hist(rounds, bins=max(rounds)-min(rounds)+1, align='left')
    plt.xlabel('Round')
    plt.ylabel('Number of Bids')
    plt.title('Bids per Round')
    plt.show()

def plot_evaluation_results(evaluations):
    """
    Plots evaluation metrics such as fairness and average distance.

    Args:
        evaluations (list): A list of evaluation results, where each result is a dictionary
                            with 'fairness' and 'avg_distance' keys.
    """
    fairness = [eval['fairness'] for eval in evaluations]
    avg_distance = [eval['avg_distance'] for eval in evaluations]

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Evaluation Instance')
    ax1.set_ylabel('Fairness', color=color)
    ax1.plot(fairness, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Average Distance', color=color)  # we already handled the x-label with ax1
    ax2.plot(avg_distance, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.title('Evaluation Results: Fairness and Average Distance')
    plt.show()

# Example usage
plot_bids_per_round(retrieve_all_bids())