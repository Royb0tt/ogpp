from flask import Blueprint, redirect, url_for, request, render_template
from ..forms import LeaderboardSelectForm
from ..export_helpers import get_leaderboard_data
from .summoner import view_with_search_bar

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/leaderboard')


@leaderboard_bp.route('/', methods=['GET', 'POST'])
@view_with_search_bar
def leaderboard(summoner_form):
    queue_type = request.args.get('queue', 'RANKED_SOLO_5x5', type=str)
    group_type = request.args.get('group', 'masters', type=str)
    select_form = LeaderboardSelectForm(queues=queue_type, groups=group_type)
    if select_form.validate_on_submit():
        return redirect(url_for('leaderboard.leaderboard',
                                group=select_form.groups.data,
                                queue=select_form.queues.data))

    leaderboard_data = get_leaderboard_data(group_type, queue_type)

    return render_template('leaderboard.html', data=leaderboard_data,
                           summoner_form=summoner_form, select_form=select_form)
